python test_create_projects_locally.py
if [[ $? = 0 ]]; then
    echo "success"
else
    echo "failure: $?"
    exit
fi

python test_initialize.py
if [[ $? = 0 ]]; then
    echo "success"
else
    echo "failure: $?"
    exit
fi

python test_create_projects.py
if [[ $? = 0 ]]; then
    echo "success"
else
    echo "failure: $?"
    exit
fi

python test_mock_results.py
if [[ $? = 0 ]]; then
    echo "success"
else
    echo "failure: $?"
    exit
fi

# python test_transfer_results.py
# if [[ $? = 0 ]]; then
#     echo "success"
# else
#     echo "failure: $?"
#     exit
# fi

python test_terminate.py
if [[ $? = 0 ]]; then
    echo "success"
else
    echo "failure: $?"
    exit
fi
