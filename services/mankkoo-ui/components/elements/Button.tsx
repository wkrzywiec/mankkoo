import { ReactNode } from "react"
import classes from "./button.module.css"

export default function Button({children, ...props}: {children: ReactNode}) {
    return (
        <div className={classes.buttonWrapper} {...props}>
            <button className={classes.button30} role="button">{children}</button>
        </div>
        
    )
}