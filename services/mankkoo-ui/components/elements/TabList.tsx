import "./TabList.css"

import { ReactNode, useEffect, useState } from "react"
import Loader from "./Loader";

const sanitizeForId = (label: string) => {
    return label
      .toLowerCase()
      .replace(/[^\w\s]|(\s+)/g, (_match: string, group1: string) =>
        group1 ? "-" : ""
      );
}

export default function TabList({labels, tabContent}: {labels: string[], tabContent: (index: number) => ReactNode}) {
    
    const [activeTab, setActiveTab] = useState<number>(0);
    const [loading, setLoading] = useState<boolean>(false); 
    const [content, setContent] = useState<ReactNode | null>(null);
    
    const handleTabClick = (index: number) => {
        setActiveTab(index);
    };

    useEffect(() => {
        const renderTabcontent = async () => {
          setLoading(true);
          try {
              setContent(tabContent(activeTab));
          } finally {
            setLoading(false);
          }
        };
    
        renderTabcontent();
      }, [activeTab, tabContent, loading, setLoading]);
    
    
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
            <div
                className="tab-panel"
                role="tabpanel"
                aria-labelledby={`tab-${sanitizeForId(labels[activeTab])}`}
                id={`panel-${sanitizeForId(labels[activeTab])}`}
            >
                {loading ? 
                    <Loader /> : 
                    content
                }   
            </div> 
            
        </div>
    )
}