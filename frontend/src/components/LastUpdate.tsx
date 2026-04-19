"use client";

interface Props {
  updatedAt: Date | null;
}

export default function LastUpdate({ updatedAt }: Props) {
  if (!updatedAt) {
    return <span className="text-xs text-[--muted]">Chargement…</span>;
  }

  return (
    <span className="text-xs text-[--muted]">
      Mise à jour :{" "}
      <time dateTime={updatedAt.toISOString()}>
        {updatedAt.toLocaleTimeString("fr-FR", { hour: "2-digit", minute: "2-digit", second: "2-digit" })}
      </time>
    </span>
  );
}
