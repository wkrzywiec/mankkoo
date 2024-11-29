import { ReactNode } from "react";
import classes from "./headline.module.css"

export default function Headline({text, children, fontSize="1.5"}: {text: string, children?: ReactNode, fontSize?: string}) {
    const styles = {fontSize: fontSize + "rem"};
    return (
        <div className={classes.headline} style={styles}>
            <h3>{text}</h3>
            {children}
        </div>
        
    )
}
