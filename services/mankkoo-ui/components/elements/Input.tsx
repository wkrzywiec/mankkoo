
import { ChangeEvent, RefObject, SyntheticEvent } from "react";
import "./Input.css";

export default function Input({
    value, 
    type = "text",
    placeholder = "...",
    onChange
} : {
    value?: string,
    type: string,
    placeholder: string,
    onChange: (e: ChangeEvent<HTMLInputElement>) => void
}) { 
    return <input className="input-data" type={type} placeholder={placeholder} value={value} onChange={onChange}></input>
}