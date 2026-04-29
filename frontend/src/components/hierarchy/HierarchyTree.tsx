import { useState } from "react";
import { ChevronDown, ChevronRight } from "lucide-react";

export interface HierarchyNode {
  id: string;
  name: string;
  type: string;
  children?: HierarchyNode[];
}

function NodeItem({ node, depth }: { node: HierarchyNode; depth: number }) {
  const [open, setOpen] = useState(depth < 1);
  const has = (node.children?.length ?? 0) > 0;
  return (
    <div>
      <div
        className="flex items-center gap-1 py-1 px-2 hover:bg-slate-100 rounded cursor-pointer text-sm"
        style={{ paddingLeft: depth * 16 + 8 }}
        onClick={() => setOpen((o) => !o)}
      >
        {has ? (open ? <ChevronDown size={14} /> : <ChevronRight size={14} />) : <span className="w-3" />}
        <span className="text-slate-500 text-xs uppercase mr-2">{node.type}</span>
        <span>{node.name}</span>
      </div>
      {open && node.children?.map((c) => <NodeItem key={c.id} node={c} depth={depth + 1} />)}
    </div>
  );
}

export function HierarchyTree({ nodes }: { nodes: HierarchyNode[] }) {
  return (
    <div className="rounded border border-slate-200 bg-white p-2">
      {nodes.map((n) => (
        <NodeItem key={n.id} node={n} depth={0} />
      ))}
    </div>
  );
}
