import type { Resource } from "@/types";
import { DataTable } from "../shared/DataTable";

export function RosterTable({ rows }: { rows: Resource[] }) {
  return (
    <DataTable<Resource>
      rows={rows}
      columns={[
        { key: "name", label: "Name" },
        { key: "role", label: "Role" },
        { key: "seniority", label: "Seniority" },
        { key: "email", label: "Email" },
      ]}
    />
  );
}
