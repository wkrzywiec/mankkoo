
import { ChangeEvent } from "react";

import classes from '@/components/elements/Input.module.css'

export default function Input({
    value, 
    type = "text",
    placeholder = "...",
    onChange
} : {
    value?: string,
    type: string,
    placeholder?: string,
    onChange: (e: ChangeEvent<HTMLInputElement>) => void
}) { 
    return <input className={classes.inputData} type={type} placeholder={placeholder} value={value} onChange={onChange}></input>
}