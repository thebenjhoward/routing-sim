import Head from 'next/head';
import React from 'react';
import styles from '../styles/Home.module.css';
import GraphGenerator from '../utils/graph_gen.js';

export default class Graph extends React.Component {
    
    constructor(props) {
        super();
        
        this.state = {
            graph: (new GraphGenerator({})).get_fresh_vis()
        };
    }
    
    render() {
        return (
        <div className={styles.container}>
            <Head>
                <title>Graph</title>
                <link rel="icon" href="/favicon.ico" />
            </Head>

            <main className={styles.main}>
                <Graph
                    graph={this.state.graph}
                    options={{layout: {hierarchical: true}, edges: { color: "#000000" }}}
                />
            </main>
        </div>
    )}
}