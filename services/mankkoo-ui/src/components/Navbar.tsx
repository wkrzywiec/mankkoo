import logo from '../assets/logo.png';
import './Navbar.css'

export function Navbar() {

    return (
        <div id="nav-bar" className="l-navbar">        
            <nav className="nav">
                <div>
                    <a href='/' className="nav_logo">
                        <img src={logo} alt='mankkoo' className="navbar-logo-image"></img>
                        <span className='nav_logo-name'>mankkoo</span>
                    </a>
                    <div className='nav_list'>
                        <a href='/' className="nav_link">
                            <i className="bx bx-grid-alt nav_icon"></i>
                            <span className='nav_name'>Overview</span>
                        </a>
                    </div>
                    <div className='nav_list'>
                        <a href='/accounts' className="nav_link">
                            <i className="bx bx-euro nav_icon"></i>
                            <span className='nav_name'>Accounts</span>
                        </a>
                    </div>
                    <div className='nav_list'>
                        <a href='/investments' className="nav_link">
                            <i className="bx bx-briefcase nav_icon"></i>
                            <span className='nav_name'>Investments</span>
                        </a>
                    </div>
                    <div className='nav_list'>
                        <a href='/debt' className="nav_link">
                            <i className="bx bx-credit-card nav_icon"></i>
                            <span className='nav_name'>Debt</span>
                        </a>
                    </div>
                    <div className='nav_list'>
                        <a href='/debt' className="nav_link">
                            <i className="bx bx-credit-card nav_icon"></i>
                            <span className='nav_name'>Debt</span>
                        </a>
                    </div>
                    <div className='nav_list'>
                        <a href='/stocks' className="nav_link">
                            <i className="bx bx-bar-chart nav_icon"></i>
                            <span className='nav_name'>Stock</span>
                        </a>
                    </div>
                    <div className='nav_list'>
                        <a href='/retirement' className="nav_link">
                            <i className="bx bx-medal nav_icon"></i>
                            <span className='nav_name'>Retirement</span>
                        </a>
                    </div>
                </div>
                <div>
                    <div className='nav_list'>
                    <a href='/settings' className="nav_link">
                        <i className="bx bx-cog nav_icon"></i>
                        <span className='nav_name'>Settings</span>
                    </a>
                    </div>
                </div>
            </nav>
        </div>
    );
}