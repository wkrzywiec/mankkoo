import { ReactNode } from "react"

const sanitizeForId = (label: string) => {
    return label
      .toLowerCase()
      .replace(/[^\w\s]|(\s+)/g, (_match: string, group1: string) =>
        group1 ? "-" : ""
      );
}

export default function TabContent({children, label}: {children: ReactNode, label: string}) {

    return (
        <div
            className="tab-panel"
            role="tabpanel"
            aria-labelledby={`tab-${sanitizeForId(label)}`}
            id={`panel-${sanitizeForId(label)}`}
        >
            {children}
        </div> 
    );
}