// Tiny keep-alive target for external cron pingers (e.g. cron-job.org).
// Deliberately outside next.config.ts's /api/:path* rewrite, so this stays
// on the frontend and never reaches the backend.
export async function GET() {
  return new Response("ok", { status: 200 });
}
