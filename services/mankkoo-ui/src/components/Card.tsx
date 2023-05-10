import React from 'react';

export function Card(props: {body: React.ReactNode, title? : string, bodyClass: string, caption?: string}) {
    return (
        <div className="card card-indicator">
            <div className={"card-body "  + props.bodyClass} >
                {
                    props.title !== undefined ? (<span className="card-body-title">{props.title}</span>) : ''
                }
                
                {props.body}
                {
                    props.caption !== undefined ? (<span className="card-indicator-caption">{props.caption}</span>) : ''
                }
                
            </div>
        </div>
    )
}