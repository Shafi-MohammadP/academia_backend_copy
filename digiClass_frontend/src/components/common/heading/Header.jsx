import React, { useState } from 'react'
import Head from './Head'
import './header.module.css'
import { NavLink } from 'react-router-dom'

const Header = () => {
    const [click, setClick] = useState(false)
  return (
    <div>
        <Head/>
        <header>
        <nav className='flexSB'>
          <ul className={click ? "mobile-nav" : "flexSB "} onClick={() => setClick(false)}>
            <li>
              <NavLink to='/'>Home</NavLink>
            </li>
            <li>
              <NavLink to='/courses'>All Courses</NavLink>
            </li>
            <li>
              <NavLink to='/about'>About</NavLink>
            </li>
            <li>
              <NavLink to='/team'>Team</NavLink>
            </li>
            <li>
              <NavLink to='/pricing'>Pricing</NavLink>
            </li>
            <li>
              <NavLink to='/journal'>Journal</NavLink>
            </li>
            <li>
              <NavLink to='/contact'>Contact</NavLink>
            </li>
          </ul>
          <div className='start'>
            <div className='button'>GET CERTIFICATE</div>
          </div>
          <button className='toggle' onClick={() => setClick(!click)}>
            {click ? <i className='fa fa-times'> </i> : <i className='fa fa-bars'></i>}
          </button>
        </nav>
      </header>
    </div>
  )
}

export default Header