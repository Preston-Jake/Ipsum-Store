import React from 'react';
import { useHistory } from "react-router-dom";

const RoundButton = (props) => {
    const history = useHistory();
    return (
    <button onClick={() => history.push(`/${props.route}`)}>{props.title}</button>
    );
}

export default RoundButton;
