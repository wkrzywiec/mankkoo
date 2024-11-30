import { ReactNode } from "react"
import classes from "./SubHeadline.module.css"

export default function SubHeadline({text}: {text: string | ReactNode}) {
    return (
        <p className={classes.tileText}>
            {text}
        </p>
    )
}