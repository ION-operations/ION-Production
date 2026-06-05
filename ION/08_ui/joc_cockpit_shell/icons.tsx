import type { SVGProps } from 'react';

const base = {
  width: 16,
  height: 16,
  viewBox: '0 0 24 24',
  fill: 'none',
  stroke: 'currentColor',
  strokeWidth: 1.7,
  strokeLinecap: 'round' as const,
  strokeLinejoin: 'round' as const,
};

export function WorkSurfaceIcon(props: SVGProps<SVGSVGElement>) {
  return <svg {...base} {...props}><path d="M4 5h16v14H4z"/><path d="M8 9h8M8 13h5"/></svg>;
}

export function ReceiptIcon(props: SVGProps<SVGSVGElement>) {
  return <svg {...base} {...props}><path d="M7 3h10v18l-2-1.5-2 1.5-2-1.5-2 1.5-2-1.5z"/><path d="M9 8h6M9 12h6M9 16h3"/></svg>;
}

export function LensIcon(props: SVGProps<SVGSVGElement>) {
  return <svg {...base} {...props}><circle cx="10.5" cy="10.5" r="5.5"/><path d="m15 15 5 5"/><path d="M8.5 10.5h4"/></svg>;
}

export function StreamIcon(props: SVGProps<SVGSVGElement>) {
  return <svg {...base} {...props}><path d="M4 7h3l2 10 3-14 2 9h6"/><path d="M4 18h16"/></svg>;
}

export function RouteIcon(props: SVGProps<SVGSVGElement>) {
  return <svg {...base} {...props}><path d="M5 5h5v5H5zM14 14h5v5h-5z"/><path d="M10 7.5h3.5a3 3 0 0 1 3 3V14"/></svg>;
}

export function GraphIcon(props: SVGProps<SVGSVGElement>) {
  return <svg {...base} {...props}><circle cx="6" cy="7" r="2"/><circle cx="18" cy="7" r="2"/><circle cx="12" cy="17" r="2"/><path d="M8 8l3 7M16 8l-3 7M8 7h8"/></svg>;
}

export function RunIcon(props: SVGProps<SVGSVGElement>) {
  return <svg {...base} {...props}><path d="M5 4v16l14-8z"/><path d="M4 20h16"/></svg>;
}

export function PauseIcon(props: SVGProps<SVGSVGElement>) {
  return <svg {...base} {...props}><path d="M7 5v14M17 5v14"/></svg>;
}

export function StopIcon(props: SVGProps<SVGSVGElement>) {
  return <svg {...base} {...props}><rect x="6" y="6" width="12" height="12" rx="1.5"/><path d="M4 20h16"/></svg>;
}

export function SystemIcon(props: SVGProps<SVGSVGElement>) {
  return <svg {...base} {...props}><rect x="7" y="7" width="10" height="10" rx="1.5"/><path d="M4 9h3M4 15h3M17 9h3M17 15h3M9 4v3M15 4v3M9 17v3M15 17v3"/></svg>;
}

export function ProjectsIcon(props: SVGProps<SVGSVGElement>) {
  return <svg {...base} {...props}><path d="M3 7h7l2 2h9v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><path d="M3 7V5a1 1 0 0 1 1-1h5l2 3"/></svg>;
}

export function AgentsIcon(props: SVGProps<SVGSVGElement>) {
  return <svg {...base} {...props}><circle cx="8" cy="8" r="3"/><circle cx="17" cy="17" r="3"/><path d="M11 9.5l3.5 3.5M5 19c1-2 2.5-3 4.5-3M14.5 5c2 0 3.5 1 4.5 3"/></svg>;
}

export function QueueIcon(props: SVGProps<SVGSVGElement>) {
  return <svg {...base} {...props}><path d="M5 6h14M5 12h14M5 18h14"/><path d="M8 4v4M12 10v4M16 16v4"/></svg>;
}

export function CodexIcon(props: SVGProps<SVGSVGElement>) {
  return <svg {...base} {...props}><rect x="3" y="4" width="18" height="16" rx="2"/><path d="m8 9 3 3-3 3M13 16h4"/></svg>;
}

export function ExtensionIcon(props: SVGProps<SVGSVGElement>) {
  return <svg {...base} {...props}><path d="M8 4h8v5h4v6h-4v5H8v-5H4V9h4z"/><path d="M10 9h4M10 15h4"/></svg>;
}

export function DocsIcon(props: SVGProps<SVGSVGElement>) {
  return <svg {...base} {...props}><path d="M6 3h9l3 3v15H6z"/><path d="M15 3v4h4M9 11h6M9 15h6M9 19h4"/></svg>;
}

export function GatesIcon(props: SVGProps<SVGSVGElement>) {
  return <svg {...base} {...props}><path d="M12 3 5 6v6c0 4 3 7 7 9 4-2 7-5 7-9V6z"/><path d="m9 12 2 2 4-5"/></svg>;
}

export function ChatIcon(props: SVGProps<SVGSVGElement>) {
  return <svg {...base} {...props}><path d="M4 5h16v11H9l-5 4z"/><path d="M8 9h8M8 13h5"/></svg>;
}

export function IdeIcon(props: SVGProps<SVGSVGElement>) {
  return <svg {...base} {...props}><rect x="3" y="4" width="18" height="16" rx="2"/><path d="M8 4v16M8 9h13M12 14h5"/></svg>;
}

export function ArchiveIcon(props: SVGProps<SVGSVGElement>) {
  return <svg {...base} {...props}><path d="M4 5h16v4H4z"/><path d="M6 9v10h12V9"/><path d="M9 13h6"/></svg>;
}

export function SettingsIcon(props: SVGProps<SVGSVGElement>) {
  return <svg {...base} {...props}><circle cx="12" cy="12" r="3"/><path d="M12 3v3M12 18v3M3 12h3M18 12h3M5.5 5.5l2.1 2.1M16.4 16.4l2.1 2.1M18.5 5.5l-2.1 2.1M7.6 16.4l-2.1 2.1"/></svg>;
}

export function HooksIcon(props: SVGProps<SVGSVGElement>) {
  return <svg {...base} {...props}><path d="M8 4v9a4 4 0 1 0 8 0v-1"/><path d="M6 4h4M14 8h4M16 6v4"/></svg>;
}

export function SkillsIcon(props: SVGProps<SVGSVGElement>) {
  return <svg {...base} {...props}><path d="M12 3l1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8z"/><path d="M5 16l.8 2.2L8 19l-2.2.8L5 22l-.8-2.2L2 19l2.2-.8z"/></svg>;
}

export function ToolsIcon(props: SVGProps<SVGSVGElement>) {
  return <svg {...base} {...props}><path d="M14.7 6.3a4 4 0 0 0-5 5L4 17v3h3l5.7-5.7a4 4 0 0 0 5-5l-2.4 2.4-3-3z"/></svg>;
}

export function TracesIcon(props: SVGProps<SVGSVGElement>) {
  return <svg {...base} {...props}><path d="M4 18h16"/><path d="M5 14l4-4 3 3 5-7 2 3"/><circle cx="9" cy="10" r="1.5"/><circle cx="17" cy="6" r="1.5"/></svg>;
}

export function BlockersIcon(props: SVGProps<SVGSVGElement>) {
  return <svg {...base} {...props}><path d="M8 3h8l5 5v8l-5 5H8l-5-5V8z"/><path d="M8 8l8 8M16 8l-8 8"/></svg>;
}

export function QuestionsIcon(props: SVGProps<SVGSVGElement>) {
  return <svg {...base} {...props}><path d="M5 5h14v10H9l-4 4z"/><path d="M10 9a2.5 2.5 0 0 1 4 2c-.3 1.2-2 1.3-2 2.7"/><circle cx="12" cy="17" r=".6"/></svg>;
}

export function AuthorityIcon(props: SVGProps<SVGSVGElement>) {
  return <svg {...base} {...props}><path d="M12 3l8 4-8 4-8-4z"/><path d="M4 12l8 4 8-4M4 17l8 4 8-4"/></svg>;
}

export function SourceIcon(props: SVGProps<SVGSVGElement>) {
  return <svg {...base} {...props}><path d="M8 4h8l4 4v12H8z"/><path d="M4 8h4M4 12h4M4 16h4M15 4v5h5"/></svg>;
}

export function HorizonIcon(props: SVGProps<SVGSVGElement>) {
  return <svg {...base} {...props}><path d="M3 16h18"/><path d="M5 16a7 7 0 0 1 14 0"/><path d="M12 5v3M6 9l2 2M18 9l-2 2"/></svg>;
}

export function DomainsIcon(props: SVGProps<SVGSVGElement>) {
  return <svg {...base} {...props}><path d="M4 4h7v7H4zM13 4h7v7h-7zM4 13h7v7H4zM13 13h7v7h-7z"/></svg>;
}

export function ComposeIcon(props: SVGProps<SVGSVGElement>) {
  return <svg {...base} {...props}><path d="M5 19h4L19 9l-4-4L5 15z"/><path d="M13 7l4 4M4 21h16"/></svg>;
}

export function SessionsIcon(props: SVGProps<SVGSVGElement>) {
  return <svg {...base} {...props}><path d="M6 5h12v14H6z"/><path d="M3 8h3M18 8h3M3 12h3M18 12h3M3 16h3M18 16h3"/></svg>;
}

export function BranchIcon(props: SVGProps<SVGSVGElement>) {
  return <svg {...base} {...props}><circle cx="6" cy="6" r="2"/><circle cx="18" cy="6" r="2"/><circle cx="12" cy="18" r="2"/><path d="M8 6h8M12 16V9a3 3 0 0 1 3-3"/></svg>;
}

export function RollbackIcon(props: SVGProps<SVGSVGElement>) {
  return <svg {...base} {...props}><path d="M8 7H4V3"/><path d="M5 7a8 8 0 1 1-1 8"/><path d="M12 8v5l4 2"/></svg>;
}

export function StatusIcon(props: SVGProps<SVGSVGElement>) {
  return <svg {...base} {...props}><path d="M4 12h4l2-6 4 12 2-6h4"/><circle cx="12" cy="12" r="9"/></svg>;
}

export function AssistantIcon(props: SVGProps<SVGSVGElement>) {
  return <svg {...base} {...props}><path d="M8 8h8v7H8z"/><path d="M12 4v4M9 18h6M6 11H4M20 11h-2"/><circle cx="10" cy="11" r=".5"/><circle cx="14" cy="11" r=".5"/></svg>;
}

export function EvidenceIcon(props: SVGProps<SVGSVGElement>) {
  return <svg {...base} {...props}><path d="M5 4h14v16H5z"/><path d="M8 9h8M8 13h8M8 17h5"/><path d="m15 5 3 3"/></svg>;
}

export function CloseIcon(props: SVGProps<SVGSVGElement>) {
  return <svg {...base} {...props}><path d="M6 6l12 12M18 6 6 18"/></svg>;
}

export function CheckIcon(props: SVGProps<SVGSVGElement>) {
  return <svg {...base} {...props}><path d="m5 12 4 4L19 6"/></svg>;
}

export function ConnectionsIcon(props: SVGProps<SVGSVGElement>) {
  return <svg {...base} {...props}><path d="M8 7H6a4 4 0 0 0 0 8h2"/><path d="M16 7h2a4 4 0 0 1 0 8h-2"/><path d="M8 12h8"/></svg>;
}

export function GmailIcon(props: SVGProps<SVGSVGElement>) {
  return <svg {...base} {...props}><path d="M4 7h16v10H4z"/><path d="M4 7l8 6 8-6"/><path d="M4 17l5-5M20 17l-5-5"/></svg>;
}

export function SupabaseIcon(props: SVGProps<SVGSVGElement>) {
  return <svg {...base} {...props}><path d="M13 3 5 13h7l-1 8 8-11h-7z"/><path d="M6 13h6M12 10h6"/></svg>;
}

export function GithubIcon(props: SVGProps<SVGSVGElement>) {
  return <svg {...base} {...props}><circle cx="12" cy="12" r="8"/><path d="M9 18v-2.5c-2.5.5-3.5-1-4-2"/><path d="M15 18v-3c0-.8-.2-1.4-.7-1.8 2-.3 3.7-1.2 3.7-4a3.4 3.4 0 0 0-.9-2.4c.1-.7 0-1.5-.3-2.3 0 0-.8-.2-2.4.9a8 8 0 0 0-4.8 0c-1.6-1.1-2.4-.9-2.4-.9-.3.8-.4 1.6-.3 2.3A3.4 3.4 0 0 0 6 9.2c0 2.8 1.7 3.7 3.7 4-.5.4-.7 1-.7 1.8V18"/></svg>;
}

export function EmailIcon(props: SVGProps<SVGSVGElement>) {
  return <svg {...base} {...props}><path d="M4 6h16v12H4z"/><path d="m4 8 8 6 8-6"/><path d="M8 18v3M16 18v3"/></svg>;
}

export function WebhookIcon(props: SVGProps<SVGSVGElement>) {
  return <svg {...base} {...props}><circle cx="7" cy="12" r="3"/><circle cx="17" cy="7" r="3"/><circle cx="17" cy="17" r="3"/><path d="M10 11l4-3M10 13l4 3"/></svg>;
}
