import classes from "./SubHeadline.module.css"

export default function SubHeadline({text}: {text: string}) {
    return (
        <p className={classes.tileText}>
            {text}
        </p>
    )
}