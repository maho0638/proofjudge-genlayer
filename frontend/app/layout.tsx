import "./globals.css";

export const metadata = {
  title: "ProofJudge — Consensus Milestone Escrow",
  description:
    "GenLayer-native milestone escrow where live evidence and validator consensus determine whether a contractor can claim locked GEN.",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
