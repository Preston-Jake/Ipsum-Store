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
          <Route path="/women" render={() => <h1>Women</h1>}/>
          <Route path="/men" render={() => <h1>Men</h1>}/>
        </Switch>
        <Nav/>
      </Router>      
  )
}

export default App;
