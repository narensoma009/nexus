import { useRef, useState } from "react";

export function UploadZone({
  accept,
  onFile,
  label = "Drop a file or click to upload",
}: {
  accept?: string;
  onFile: (f: File) => void;
  label?: string;
}) {
  const [drag, setDrag] = useState(false);
  const ref = useRef<HTMLInputElement>(null);
  return (
    <div
      onDragOver={(e) => {
        e.preventDefault();
        setDrag(true);
      }}
      onDragLeave={() => setDrag(false)}
      onDrop={(e) => {
        e.preventDefault();
        setDrag(false);
        if (e.dataTransfer.files[0]) onFile(e.dataTransfer.files[0]);
      }}
      onClick={() => ref.current?.click()}
      className={`border-2 border-dashed rounded p-6 text-center text-sm cursor-pointer ${
        drag ? "border-brand-500 bg-cyan-50" : "border-slate-300 bg-white"
      }`}
    >
      <input
        ref={ref}
        type="file"
        accept={accept}
        className="hidden"
        onChange={(e) => e.target.files?.[0] && onFile(e.target.files[0])}
      />
      {label}
    </div>
  );
}
