import "./TabList.css"

import { ReactElement, useState } from "react"
import TabContent from "./TabContent";

const sanitizeForId = (label: string) => {
    return label
      .toLowerCase()
      .replace(/[^\w\s]|(\s+)/g, (_match: string, group1: string) =>
        group1 ? "-" : ""
      );
}

export default function TabList({children, activeTabIndex = 0}: {children: ReactElement<typeof TabContent>[], activeTabIndex?: number}) {
    
    const [activeTab, setActiveTab] = useState(activeTabIndex);
    const handleTabClick = (index: number) => {
        setActiveTab(index);
    };

    const labels = children
        .map(tab => tab.props as { [key: string]: any })
        .map(tabProps => tabProps.label as string)
    
    return (
        <div className="tabs">
            <nav className="tab-list-wrapper">
                <ul className="tab-list" role="tablist" aria-orientation="horizontal">
                {labels.map((label, index) => (
                    <li key={`tab-${index}`}>
                        <button
                            key={`tab-btn-${index}`}
                            role="tab"
                            id={`tab-${sanitizeForId(label)}`}
                            aria-controls={`panel-${sanitizeForId(label)}`}
                            aria-selected={activeTab === index}
                            onClick={() => handleTabClick(index)}
                            className={`tab-btn ${
                                activeTab === index && "tab-btn--active"
                            }`}
                        >{label}</button>
                    </li>
                ))}
                </ul>
            </nav>
            {children[activeTab]}
        </div>
    )
}