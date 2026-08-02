const paths: Record<string, string> = {
  overview: "M4 4h6v6H4zM14 4h6v6h-6zM4 14h6v6H4zM14 14h6v6h-6z",
  detect: "M4 8V4h4M16 4h4v4M20 16v4h-4M8 20H4v-4M8 12h8",
  chart: "M4 19V9m6 10V5m6 14v-7m4 7H2",
  errors: "M12 3 4 7v10l8 4 8-4V7l-8-4Zm0 5v5m0 4h.01",
  model: "M5 5h14v5H5zM5 14h6v5H5zM15 14h4v5h-4z",
  scope: "M12 3 4.5 6v5.5c0 4.7 3.2 8 7.5 9.5 4.3-1.5 7.5-4.8 7.5-9.5V6L12 3Z"
};

export function Icon({ name }: { name: string }) {
  return <svg aria-hidden="true" viewBox="0 0 24 24"><path d={paths[name]} /></svg>;
}
