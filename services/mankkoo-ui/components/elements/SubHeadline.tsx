import classes from "./SubHeadline.module.css"
import { ReactNode } from 'react';

export default function SubHeadline({children}: {children: ReactNode}) {
    return (
        <p className={classes.tileText}>
            {children}
        </p>
    )
}