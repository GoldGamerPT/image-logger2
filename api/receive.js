export default function handler(req, res) {
  if (req.method !== "POST") {
    return res.status(405).end();
  }

  const { data } = req.body;

  // validate input
  if (typeof data !== "string") {
    return res.status(400).json({ error: "Invalid data" });
  }

  // store / process / return
  res.status(200).json({ ok: true });
}
