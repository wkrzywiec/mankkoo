import classes from "./tile-header.module.css"
import Headline from "@/components/elements/headline"
import { ReactNode } from 'react';

export default function TileHeader({headline, children}: {headline: string, children: ReactNode}) {
    return (
        <>
            <Headline text={headline} fontSize="2" />
            <p className={classes.tileText}>
                {children}
            </p>
        </>
    )
}