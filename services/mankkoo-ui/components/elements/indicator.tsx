import classes from './indicator.module.css'

export default function Indicator({headline, text, textColor="var(--font-color)"}: {headline: string, text: string, textColor: string}) {
    return (
        <>
            <h3 className={classes.indicatorHeadline}>{headline}</h3>
            <p className={classes.indicatorText} style={{color: textColor}}>{text}</p>
        </>
    )
}