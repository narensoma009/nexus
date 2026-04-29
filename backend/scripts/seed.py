"""Seed the database with realistic AT&T-flavored sample data.

Usage (from backend/ with venv active):
    python -m scripts.seed                          # default: skip if data exists
    python -m scripts.seed --reset                  # wipe all rows first
    python -m scripts.seed --my-oid <entra-oid>     # also create an account_admin user_role for you

Generates:
- 1 Account (AT&T)
- 3 Portfolios (Network, Consumer, Enterprise) + 2 sub-portfolios
- ~12 Teams (some nested)
- 45 Resources across teams
- 4 Programs with projects, workstreams, and resource assignments
- 5 AI Tools with licenses and 30 days of usage data
"""
import argparse
import asyncio
import random
import uuid
from datetime import datetime, timedelta

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal
from app.models import (
    Account, Portfolio, SubPortfolio, Team,
    Resource, UserRole,
    Program, Project, Workstream, ResourceAssignment,
    AITool, AIToolLicense, AIToolUsage,
)


FIRST_NAMES = [
    "Aarav", "Priya", "Liam", "Sofia", "Noah", "Mia", "Kai", "Zara",
    "Diego", "Anika", "Marcus", "Layla", "Owen", "Ines", "Theo", "Nia",
    "Ezra", "Maya", "Felix", "Ravi", "Yara", "Jonas", "Iris", "Soren",
    "Aisha", "Mateo", "Lucia", "Aksel", "Elif", "Nico", "Hana", "Idris",
    "Ines", "Tariq", "Naomi", "Kenji", "Maeve", "Rahul", "Suki", "Omar",
    "Aria", "Bran", "Cleo", "Dario", "Esme",
]
LAST_NAMES = [
    "Patel", "Garcia", "Smith", "Chen", "Singh", "Rossi", "Kim", "Khan",
    "Müller", "Tanaka", "Jensen", "Nguyen", "Martinez", "Cohen", "Walker",
    "O'Brien", "Reyes", "Sato", "Andersson", "Bennett", "Diaz", "Schmidt",
]
ROLES = [
    ("Solution Architect", "senior"),
    ("Senior Developer", "senior"),
    ("Developer", "mid"),
    ("Junior Developer", "junior"),
    ("QA Engineer", "mid"),
    ("DevOps Engineer", "senior"),
    ("Data Engineer", "mid"),
    ("Product Manager", "senior"),
    ("Business Analyst", "mid"),
    ("Tech Lead", "lead"),
    ("Scrum Master", "mid"),
    ("UX Designer", "mid"),
]
SKILLS = [
    "Python,FastAPI,PostgreSQL", "Java,Spring,Kafka", "React,TypeScript,GraphQL",
    "Go,gRPC,Kubernetes", "Snowflake,dbt,Airflow", "Databricks,Spark,Delta",
    "AWS,Terraform,EKS", "Azure,Bicep,AKS", ".NET,C#,Azure",
    "Salesforce,Apex,LWC", "ServiceNow,JavaScript", "Tableau,PowerBI",
]


def fake_email(first: str, last: str, n: int) -> str:
    return f"{first.lower()}.{last.lower().replace(chr(39), '')}{n}@accenture.com"


async def reset(db: AsyncSession):
    # Order matters due to FKs
    for model in [
        ResourceAssignment, Workstream, Project, Program,
        AIToolUsage, AIToolLicense, AITool,
        UserRole, Resource, Team, SubPortfolio, Portfolio, Account,
    ]:
        await db.execute(delete(model))
    await db.commit()
    print("[reset] cleared all rows")


async def seed_hierarchy(db: AsyncSession) -> tuple[Account, list[Portfolio], list[Team]]:
    account = Account(name="AT&T")
    db.add(account)
    await db.flush()

    portfolios_data = [
        ("Network", "Wireless and wireline network engineering"),
        ("Consumer", "Consumer mobility, broadband, and video products"),
        ("Enterprise", "Business and enterprise solutions"),
    ]
    portfolios = [Portfolio(account_id=account.id, name=n, description=d) for n, d in portfolios_data]
    db.add_all(portfolios)
    await db.flush()

    # Sub-portfolios under Consumer
    consumer = portfolios[1]
    subs = [
        SubPortfolio(portfolio_id=consumer.id, name="Mobility", description="Wireless consumer products"),
        SubPortfolio(portfolio_id=consumer.id, name="Broadband", description="Fiber and home internet"),
    ]
    db.add_all(subs)
    await db.flush()

    teams: list[Team] = []

    # Network teams
    network = portfolios[0]
    net_core = Team(name="Core Network Engineering", portfolio_id=network.id)
    net_radio = Team(name="Radio Access Network", portfolio_id=network.id)
    net_ops = Team(name="Network Operations", portfolio_id=network.id)
    db.add_all([net_core, net_radio, net_ops])
    await db.flush()
    # Sub-team under Core
    net_core_sdn = Team(name="SDN Platform", portfolio_id=network.id, parent_team_id=net_core.id)
    db.add(net_core_sdn)
    teams += [net_core, net_radio, net_ops, net_core_sdn]

    # Consumer Mobility teams
    mob = subs[0]
    mob_app = Team(name="Mobility App", sub_portfolio_id=mob.id)
    mob_billing = Team(name="Mobility Billing", sub_portfolio_id=mob.id)
    db.add_all([mob_app, mob_billing])
    teams += [mob_app, mob_billing]

    # Consumer Broadband teams
    bb = subs[1]
    bb_fiber = Team(name="Fiber Provisioning", sub_portfolio_id=bb.id)
    bb_care = Team(name="Broadband Care", sub_portfolio_id=bb.id)
    db.add_all([bb_fiber, bb_care])
    teams += [bb_fiber, bb_care]

    # Enterprise teams
    ent = portfolios[2]
    ent_security = Team(name="Enterprise Security", portfolio_id=ent.id)
    ent_cloud = Team(name="Cloud Solutions", portfolio_id=ent.id)
    ent_iot = Team(name="IoT Platform", portfolio_id=ent.id)
    db.add_all([ent_security, ent_cloud, ent_iot])
    await db.flush()
    # Sub-team under Cloud
    ent_cloud_data = Team(name="Cloud Data Engineering", portfolio_id=ent.id, parent_team_id=ent_cloud.id)
    db.add(ent_cloud_data)
    teams += [ent_security, ent_cloud, ent_iot, ent_cloud_data]

    await db.flush()
    print(f"[hierarchy] account={account.name}, portfolios={len(portfolios)}, sub_portfolios={len(subs)}, teams={len(teams)}")
    return account, portfolios, teams


async def seed_resources(db: AsyncSession, teams: list[Team]) -> list[Resource]:
    resources: list[Resource] = []
    used_emails: set[str] = set()

    for team in teams:
        n_members = random.randint(2, 6)
        for _ in range(n_members):
            first = random.choice(FIRST_NAMES)
            last = random.choice(LAST_NAMES)
            role, seniority = random.choice(ROLES)
            counter = 0
            while True:
                email = fake_email(first, last, counter)
                if email not in used_emails:
                    used_emails.add(email)
                    break
                counter += 1
            r = Resource(
                team_id=team.id,
                name=f"{first} {last}",
                email=email,
                role=role,
                seniority=seniority,
                skills=random.choice(SKILLS),
                is_active=True,
            )
            resources.append(r)
    db.add_all(resources)
    await db.flush()
    print(f"[resources] created {len(resources)} resources")
    return resources


async def seed_programs(
    db: AsyncSession, account: Account, resources: list[Resource]
) -> list[Program]:
    program_specs = [
        ("5G Core Modernization", "Migrate legacy core network functions to cloud-native 5G stack", "on_track"),
        ("FirstNet Expansion", "Expand FirstNet public-safety coverage and capabilities", "at_risk"),
        ("Fiber Acceleration", "Accelerate fiber footprint to 30M consumer locations", "on_track"),
        ("Enterprise AI Platform", "Build enterprise-wide AI/ML platform on Azure + Databricks", "planning"),
    ]
    programs: list[Program] = []
    today = datetime.utcnow()

    for name, desc, status in program_specs:
        p = Program(
            account_id=account.id,
            name=name,
            description=desc,
            status=status,
            start_date=today - timedelta(days=random.randint(30, 365)),
            end_date=today + timedelta(days=random.randint(180, 720)),
        )
        programs.append(p)
    db.add_all(programs)
    await db.flush()

    project_count = 0
    workstream_count = 0
    assignment_count = 0

    for prog in programs:
        n_projects = random.randint(2, 4)
        for pi in range(n_projects):
            proj = Project(program_id=prog.id, name=f"{prog.name} - Phase {pi + 1}",
                           status=random.choice(["on_track", "on_track", "on_track", "at_risk"]))
            db.add(proj)
            await db.flush()
            project_count += 1

            n_streams = random.randint(2, 4)
            for si in range(n_streams):
                ws = Workstream(project_id=proj.id,
                                name=random.choice([
                                    "Backend services", "Data platform", "Frontend UX",
                                    "Migration", "Testing & QA", "Security review",
                                    "Integration", "Deployment", "Documentation",
                                ]) + f" {si + 1}",
                                status=random.choice(["on_track", "on_track", "at_risk"]))
                db.add(ws)
                await db.flush()
                workstream_count += 1

                # Assign 3-7 resources per workstream
                assigned = random.sample(resources, k=random.randint(3, 7))
                for r in assigned:
                    a = ResourceAssignment(
                        resource_id=r.id,
                        workstream_id=ws.id,
                        role=r.role,
                        allocation_pct=random.choice([20, 30, 50, 50, 75, 100]),
                        start_date=today - timedelta(days=random.randint(30, 200)),
                        end_date=today + timedelta(days=random.randint(60, 365)),
                    )
                    db.add(a)
                    assignment_count += 1

    await db.flush()
    print(f"[programs] created {len(programs)} programs, {project_count} projects, "
          f"{workstream_count} workstreams, {assignment_count} assignments")
    return programs


async def seed_ai_adoption(db: AsyncSession, resources: list[Resource]):
    tool_specs = [
        ("GitHub Copilot", "GitHub", "code_assist"),
        ("Claude Code", "Anthropic", "agentic"),
        ("Cursor", "Anysphere", "code_assist"),
        ("ChatGPT Enterprise", "OpenAI", "doc_gen"),
        ("Databricks Genie", "Databricks", "data"),
    ]
    tools = [
        AITool(
            name=n, vendor=v, category=c,
            rollout_date=datetime.utcnow() - timedelta(days=random.randint(60, 540)),
            target_user_count=random.choice([100, 250, 500, 1000]),
        )
        for n, v, c in tool_specs
    ]
    db.add_all(tools)
    await db.flush()

    license_count = 0
    for tool in tools:
        # Each tool licensed to 30-70% of resources
        sample_size = max(1, int(len(resources) * random.uniform(0.3, 0.7)))
        sampled = random.sample(resources, sample_size)
        for r in sampled:
            lic = AIToolLicense(
                tool_id=tool.id,
                resource_id=r.id,
                assigned_date=datetime.utcnow() - timedelta(days=random.randint(7, 365)),
                adoption_stage=random.choices(
                    ["piloting", "onboarded", "active", "embedded"],
                    weights=[1, 2, 3, 2],
                )[0],
            )
            db.add(lic)
            license_count += 1

    # Usage data: last 30 days
    usage_count = 0
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    for tool in tools:
        active_users = random.sample(resources, k=int(len(resources) * 0.4))
        for day_offset in range(30):
            day = today - timedelta(days=day_offset)
            # Sample subset of users per day
            daily = random.sample(active_users, k=int(len(active_users) * random.uniform(0.4, 0.9)))
            for r in daily:
                u = AIToolUsage(
                    tool_id=tool.id,
                    resource_id=r.id,
                    recorded_date=day,
                    sessions=random.randint(1, 12),
                    active_minutes=random.randint(5, 240),
                    source="api" if random.random() > 0.3 else "manual",
                )
                db.add(u)
                usage_count += 1

    await db.flush()
    print(f"[ai_adoption] {len(tools)} tools, {license_count} licenses, {usage_count} usage events")


async def seed_user_role(db: AsyncSession, oid: str | None):
    if not oid:
        return
    res = await db.execute(select(UserRole).where(UserRole.entra_oid == oid))
    existing = res.scalar_one_or_none()
    if existing:
        existing.role = "account_admin"
        existing.scope_id = None
    else:
        db.add(UserRole(entra_oid=oid, role="account_admin"))
    await db.flush()
    print(f"[user_role] account_admin role assigned to oid={oid}")


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action="store_true", help="Wipe all rows before seeding")
    parser.add_argument("--my-oid", default=None, help="Entra OID to grant account_admin")
    args = parser.parse_args()

    random.seed(42)

    async with AsyncSessionLocal() as db:
        if args.reset:
            await reset(db)
        else:
            existing = (await db.execute(select(Account))).scalar_one_or_none()
            if existing:
                print(f"[skip] data already exists (account={existing.name}). Use --reset to wipe.")
                return

        account, portfolios, teams = await seed_hierarchy(db)
        resources = await seed_resources(db, teams)
        await seed_programs(db, account, resources)
        await seed_ai_adoption(db, resources)
        await seed_user_role(db, args.my_oid)

        await db.commit()
        print("\n[done] seed complete.")


if __name__ == "__main__":
    asyncio.run(main())
