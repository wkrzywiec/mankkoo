import classes from "./Indicator.module.css"
import Headline from "@/components/elements/Headline"

export default function Indicator({headline, text, textColor="var(--font-color)"}: {headline: string, text: string, textColor?: string}) {
    return (
        <>
            <Headline text={headline} />
            <p className={classes.indicatorText} style={{color: textColor}}>{text}</p>
        </>
    )
}