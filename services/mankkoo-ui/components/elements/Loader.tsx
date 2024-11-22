import classes from '@/components/elements/Loader.module.css'

export default function Loader({height=200} : {height: number}) {
    const heightInPx = height.toString() + "px"
    return (
        <div className={classes.loaderContainer} style={{height: heightInPx}}>
            <span className={classes.loader}></span>
        </div>
        
    )
}