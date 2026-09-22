import "./globals.css";

export const metadata = {
  title: "ProofJudge — GenLayer Evidence Verification",
  description: "Consensus-backed review of public task evidence.",
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
