import { ReactNode, SyntheticEvent } from "react"
import classes from "./Button.module.css"

export default function Button({children, onClick, id}: {children: ReactNode, onClick: (event: SyntheticEvent<Element, Event>) => void, id?: string}) {
    return (
        <div className={classes.buttonWrapper} onClick={onClick}>
            <button className={classes.button30} role="button" id={id}>{children}</button>
        </div>
        
    )
}