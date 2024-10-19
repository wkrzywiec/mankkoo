import classes from "./headline.module.css"

export default function Headline({text, fontSize="1.5"}: {text: string, fontSize?: string}) {
    const styles = {fontSize: fontSize + "rem"};
    return (
        <h3 className={classes.headline} style={styles}>{text}</h3>
    )
}