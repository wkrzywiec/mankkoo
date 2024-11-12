import { ReactNode } from "react"
import classes from "./button.module.css"

export default function Button({children}: {children: ReactNode}) {
    return (
        <div className={classes.buttonWrapper}>
            <button className={classes.button30} role="button">{children}</button>
        </div>
        
    )
}