import React, { useState, useEffect } from 'react';
import './App.css';

import {BrowserRouter as Router, Route, Switch} from 'react-router-dom'

import IpsumStore from './IpsumStore'
import Nav from './Nav';


function App() {
  return(
      <Router>
        <Switch>
          <Route path="/" exact component={IpsumStore}/>
        </Switch>
        <Nav/>
      </Router>      
  )
}

export default App;
