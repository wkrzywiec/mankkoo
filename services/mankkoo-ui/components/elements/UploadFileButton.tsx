import { ChangeEvent } from "react"
import classes from "./Button.module.css"

export type HandleFileUploadCallback = (e: ChangeEvent<HTMLInputElement>) => (void);

export default function UploadFileButton({handleUpload, id, btnText, ...props}: {handleUpload: HandleFileUploadCallback, id: string, btnText: string}) {
    return (
        <div className={classes.buttonWrapper} {...props}>
            <label htmlFor={id} className={classes.button30}>{btnText}</label>
            <input type="file" id={id} hidden onChange={handleUpload}/>
        </div>
        
    )
}