import { ReactNode, SyntheticEvent } from "react";
import "./Modal.css";
import Button from "./Button";
import TileHeader from "./TileHeader";

export default function Modal(
    { isOpen, header, subHeader, onSubmit, onClose, children }:
    {isOpen: boolean, header: string, subHeader?: string, onSubmit: (event: SyntheticEvent<Element, Event>) => void, onClose: () => void, children?: ReactNode}) {
  if (!isOpen) return null;

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <TileHeader headline={header} subHeadline={subHeader} />
        <div >
            {children}
        </div>
        <div className="buttons-content">
            <Button onClick={onSubmit} value="">Submit</Button>
            <Button onClick={onClose} value="">Close</Button>
        </div>
      </div>
    </div>
  );
};
