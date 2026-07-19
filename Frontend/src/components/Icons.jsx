// Lightweight stroke-icon set (Feather-style) used across SmartSweep.
// Kept in one file so the visual language stays consistent everywhere.

const base = {
  viewBox: "0 0 24 24",
  fill: "none",
  stroke: "currentColor",
  strokeWidth: 1.8,
  strokeLinecap: "round",
  strokeLinejoin: "round",
};

export const IconHome = (props) => (
  <svg {...base} {...props}>
    <path d="M3 11.5 12 4l9 7.5" />
    <path d="M5.5 9.5V20h13V9.5" />
    <path d="M9.5 20v-6h5v6" />
  </svg>
);

export const IconReport = (props) => (
  <svg {...base} {...props}>
    <circle cx="12" cy="12" r="9" />
    <path d="M12 7.5v9M7.5 12h9" />
  </svg>
);

export const IconClipboard = (props) => (
  <svg {...base} {...props}>
    <rect x="5.5" y="4.5" width="13" height="16" rx="2" />
    <path d="M9 4.5h6a1 1 0 0 1 1 1V6H8V5.5a1 1 0 0 1 1-1Z" />
    <path d="M8.5 11h7M8.5 14.5h7M8.5 18h4" />
  </svg>
);

export const IconBroom = (props) => (
  <svg {...base} {...props}>
    <path d="M20 4 10.5 13.5" />
    <path d="M9 12 4 20l3 1 2.5-3.5" />
    <path d="M9 12c-1-1.4-.7-3 .6-4.1 1.4-1.2 3.4-1 4.4.4l1 1.4-3.9 3.3-2.1-1Z" />
  </svg>
);

export const IconGrid = (props) => (
  <svg {...base} {...props}>
    <rect x="4" y="4" width="7" height="7" rx="1.4" />
    <rect x="13" y="4" width="7" height="7" rx="1.4" />
    <rect x="4" y="13" width="7" height="7" rx="1.4" />
    <rect x="13" y="13" width="7" height="7" rx="1.4" />
  </svg>
);

export const IconLogOut = (props) => (
  <svg {...base} {...props}>
    <path d="M9 4.5H6a1.5 1.5 0 0 0-1.5 1.5v12A1.5 1.5 0 0 0 6 19.5h3" />
    <path d="M14.5 16 19 12l-4.5-4" />
    <path d="M19 12H9" />
  </svg>
);

export const IconSun = (props) => (
  <svg {...base} {...props}>
    <circle cx="12" cy="12" r="4" />
    <path d="M12 3v2M12 19v2M4.2 4.2l1.4 1.4M18.4 18.4l1.4 1.4M3 12h2M19 12h2M4.2 19.8l1.4-1.4M18.4 5.6l1.4-1.4" />
  </svg>
);

export const IconMoon = (props) => (
  <svg {...base} {...props}>
    <path d="M20 14.5A8.5 8.5 0 1 1 9.5 4 6.8 6.8 0 0 0 20 14.5Z" />
  </svg>
);

export const IconPin = (props) => (
  <svg {...base} {...props}>
    <path d="M12 21s-6.5-6.1-6.5-11A6.5 6.5 0 0 1 18.5 10c0 4.9-6.5 11-6.5 11Z" />
    <circle cx="12" cy="10" r="2.3" />
  </svg>
);

export const IconCamera = (props) => (
  <svg {...base} {...props}>
    <path d="M4 8.5A1.5 1.5 0 0 1 5.5 7h2l1-2h7l1 2h2A1.5 1.5 0 0 1 20 8.5v9A1.5 1.5 0 0 1 18.5 19h-13A1.5 1.5 0 0 1 4 17.5v-9Z" />
    <circle cx="12" cy="12.5" r="3.4" />
  </svg>
);

export const IconCheckCircle = (props) => (
  <svg {...base} {...props}>
    <circle cx="12" cy="12" r="8.5" />
    <path d="M8.5 12.3 11 14.7l4.8-5.4" />
  </svg>
);

export const IconUserPlus = (props) => (
  <svg {...base} {...props}>
    <circle cx="10" cy="9" r="3.2" />
    <path d="M4.5 19c.6-3 2.8-4.7 5.5-4.7s4.9 1.7 5.5 4.7" />
    <path d="M18 8.5v5M15.5 11h5" />
  </svg>
);

export const IconAlertTriangle = (props) => (
  <svg {...base} {...props}>
    <path d="M12 4.5 21 19.5H3L12 4.5Z" />
    <path d="M12 10v4.2M12 17v.01" />
  </svg>
);

export const IconArrowRight = (props) => (
  <svg {...base} {...props}>
    <path d="M4.5 12h14.5M13.5 6.5 20 12l-6.5 5.5" />
  </svg>
);

export const IconAlertCircle = (props) => (
  <svg {...base} {...props}>
    <circle cx="12" cy="12" r="8.5" />
    <path d="M12 8v4.5M12 16v.01" />
  </svg>
);
