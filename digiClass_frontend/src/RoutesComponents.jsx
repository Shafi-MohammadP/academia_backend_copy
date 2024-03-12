import React from 'react'
import { Route, Routes } from 'react-router-dom'
import StudentRoutes from './routes/StudentRoutes'
import TutorRoutes from './routes/TutorRoutes'
import Adminroutes from './routes/Adminroutes'

function RoutesComponents() {
    return (
        <Routes>
            <Route path='/*' 
            element={StudentRoutes}/>
    
            <Route path='/tutor/'
            element={TutorRoutes}/>
    
            <Route path='/admin/' 
            element={Adminroutes}/>
    
        </Routes>
      )
}

export default RoutesComponents