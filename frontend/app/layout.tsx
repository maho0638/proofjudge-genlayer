import "./globals.css";

export const metadata = {
  title: "ProofJudge — Consensus Milestone Escrow",
  description:
    "GenLayer-native milestone escrow where live evidence and validator consensus determine whether a contractor can claim locked GEN.",
  icons: {
    icon: "/proofjudge-logo.png",
    shortcut: "/proofjudge-logo.png",
    apple: "/proofjudge-logo.png",
  },
  openGraph: {
    title: "ProofJudge — Consensus Milestone Escrow",
    description:
      "Live evidence and GenLayer validator consensus determine whether escrowed GEN can be claimed.",
    images: ["/proofjudge-logo.png"],
  },
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
