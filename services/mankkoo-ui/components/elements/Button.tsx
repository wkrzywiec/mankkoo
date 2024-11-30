import { ReactNode, SyntheticEvent } from "react"
import classes from "./Button.module.css"

export default function Button({children, onClick, value}: {children: ReactNode, onClick: (event: SyntheticEvent<Element, Event>) => void, value: string}) {
    return (
        <div className={classes.buttonWrapper} onClick={onClick}>
            <button className={classes.button30} role="button" value={value}>{children}</button>
        </div>
        
    )
}