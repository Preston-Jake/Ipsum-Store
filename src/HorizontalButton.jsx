import React, { useState } from 'react';
import { useHistory } from "react-router-dom";

const HorizontalButton = (props) => {
    const history = useHistory();
    return (
    <button onClick={() => history.push(`/${props.route}`)}>{props.title}</button>
    );
}

export default HorizontalButton;
