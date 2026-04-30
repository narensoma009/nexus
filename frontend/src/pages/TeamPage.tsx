import { useParams } from "@tanstack/react-router";
import { useTeam, useTeamMembers } from "@/hooks/useHierarchyNode";
import { Breadcrumb } from "@/components/layout/Breadcrumb";
import { RosterTable } from "@/components/resources/RosterTable";
import { asArray } from "@/utils/array";

export function TeamPage() {
  const { teamId } = useParams({ from: "/teams/$teamId" });
  const { data: team } = useTeam(teamId);
  const { data: members } = useTeamMembers(teamId);

  if (!team) return <div className="text-slate-500">Loading…</div>;

  return (
    <div className="space-y-6">
      <Breadcrumb items={[{ label: "Teams" }, { label: team.name }]} />
      <h1 className="text-2xl font-semibold">{team.name}</h1>

      <section>
        <h2 className="font-semibold mb-2">Members</h2>
        <RosterTable rows={asArray(members)} />
      </section>
    </div>
  );
}
