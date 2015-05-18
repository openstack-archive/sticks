# sticks.sh - Devstack extras script to install Sticks

if is_service_enabled sticks-api sticks-agent; then
    if [[ "$1" == "source" ]]; then
        # Initial source
        source $TOP_DIR/lib/sticks
    elif [[ "$1" == "stack" && "$2" == "install" ]]; then
        echo_summary "Installing Sticks"
        install_sticks
        install_sticksclient

        if is_service_enabled sticks-dashboard; then
            install_sticksdashboard
        fi
        cleanup_sticks
    elif [[ "$1" == "stack" && "$2" == "post-config" ]]; then
        echo_summary "Configuring Sticks"
        configure_sticks
        if is_service_enabled sticks-dashboard; then
            configure_sticksdashboard
        fi
        if is_service_enabled key; then
            create_sticks_accounts
        fi

    elif [[ "$1" == "stack" && "$2" == "extra" ]]; then
        # Initialize sticks
        echo_summary "Initializing Sticks"
        init_sticks

        # Start the Sticks API and Sticks agent components
        echo_summary "Starting Sticks"
        start_sticks
    fi

    if [[ "$1" == "unstack" ]]; then
        stop_sticks
    fi
fi
