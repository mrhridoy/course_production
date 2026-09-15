import { Card, CardContent } from "@/components/ui/card";

interface StatCardProps {
  label: string;
  value: string | number;
  hint?: string;
}

export function StatCard({ label, value, hint }: StatCardProps) {
  return (
    <Card>
      <CardContent className="space-y-1">
        <p className="text-xs uppercase tracking-wide text-neutral-500">{label}</p>
        <p className="text-2xl font-semibold text-neutral-900">{value}</p>
        {hint && <p className="text-xs text-neutral-500">{hint}</p>}
      </CardContent>
    </Card>
  );
}
