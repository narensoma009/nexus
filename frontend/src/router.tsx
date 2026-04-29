import {
  createRouter,
  createRoute,
  createRootRoute,
  Outlet,
} from "@tanstack/react-router";
import { AppShell } from "./components/layout/AppShell";
import { AuthGate } from "./auth/AuthProvider";
import { ProgramsPage } from "./pages/ProgramsPage";
import { ProgramDetailPage } from "./pages/ProgramDetailPage";
import { PortfolioPage } from "./pages/PortfolioPage";
import { TeamPage } from "./pages/TeamPage";
import { ResourcePage } from "./pages/ResourcePage";
import { AIAdoptionPage } from "./pages/AIAdoptionPage";
import { SlideGeneratorPage } from "./pages/SlideGeneratorPage";
import { ChatPage } from "./pages/ChatPage";
import { AdminPage } from "./pages/AdminPage";

const rootRoute = createRootRoute({
  component: () => (
    <AuthGate>
      <AppShell>
        <Outlet />
      </AppShell>
    </AuthGate>
  ),
});

const indexRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/",
  component: ProgramsPage,
});
const programDetailRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/programs/$programId",
  component: ProgramDetailPage,
});
const portfolioRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/portfolios/$portfolioId",
  component: PortfolioPage,
});
const teamRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/teams/$teamId",
  component: TeamPage,
});
const resourceRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/resources/$resourceId",
  component: ResourcePage,
});
const adoptionRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/ai-adoption",
  component: AIAdoptionPage,
});
const slidesRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/slides",
  component: SlideGeneratorPage,
});
const chatRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/chat",
  component: ChatPage,
});
const adminRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/admin",
  component: AdminPage,
});

const routeTree = rootRoute.addChildren([
  indexRoute,
  programDetailRoute,
  portfolioRoute,
  teamRoute,
  resourceRoute,
  adoptionRoute,
  slidesRoute,
  chatRoute,
  adminRoute,
]);

export const router = createRouter({ routeTree });

declare module "@tanstack/react-router" {
  interface Register {
    router: typeof router;
  }
}
