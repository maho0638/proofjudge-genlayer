import "./globals.css";

export const metadata = {
  title: "ProofJudge — Consensus Milestone Escrow",
  description:
    "GenLayer-native milestone escrow where live evidence and validator consensus determine whether a contractor can claim locked GEN.",
  icons: {
    icon: "/proofjudge-logo.webp",
    shortcut: "/proofjudge-logo.webp",
    apple: "/proofjudge-logo.webp",
  },
  openGraph: {
    title: "ProofJudge — Consensus Milestone Escrow",
    description:
      "Live evidence and GenLayer validator consensus determine whether escrowed GEN can be claimed.",
    images: ["/proofjudge-logo.webp"],
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
