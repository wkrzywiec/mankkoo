import classes from "./tile-header.module.css"
import Headline from "@/components/elements/headline"

export default function TileHeader({headline, text}: {headline: string, text: string}) {
    return (
        <>
            <Headline text={headline} fontSize="2" />
            <p className={classes.tileText}>{text}</p>
        </>
    )
}