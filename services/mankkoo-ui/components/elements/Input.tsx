
import { SyntheticEvent } from "react";
import "./Input.css";

export default function Input(
    value: string,
    onChange: (event: SyntheticEvent<Element, Event>) => void
) { 
    return <input className="input-data" type="text" value={value} onChange={onChange}></input>
}