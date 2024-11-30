import classes from "./Indicator.module.css"
import Headline from "@/components/elements/Headline"

export default function Indicator({headline, text, textColor="var(--font-color)", isFetching=false}: {headline: string, text: string, textColor?: string, isFetching?: boolean}) {
    return (
        <>
            <Headline text={headline} />
            <p className={classes.indicatorText} style={{color: textColor}}>{isFetching ? 'Loading...' : text}</p>
        </>
    )
}
