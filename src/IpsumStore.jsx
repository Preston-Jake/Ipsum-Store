import React from 'react';
import TopNav from './TopNav'
import HorizontalButton from './HorizontalButton';
const IpsumStore = () => {
    return (
        <div className="ipsum_store">
              <TopNav/>
              <section className="">
                <h2>Modern Clothing</h2>
                <h2>For</h2>
                <h2>Today's People </h2>
              </section>
              <section>
                  <HorizontalButton route='women' title="Shop Women"/>
                  <HorizontalButton route='men' title="Shop Men"/>
              </section>
                  <p>carousel</p> 
        </div>
    );
}

export default IpsumStore;
