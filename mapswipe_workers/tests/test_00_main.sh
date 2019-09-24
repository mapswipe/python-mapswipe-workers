python test_02_create_projects.py
if [[ $? = 0 ]]; then
    echo "success"
else
    echo "failure: $?"
    exit
fi


python test_03_mapping.py
if [[ $? = 0 ]]; then
    echo "success"
else
    echo "failure: $?"
    exit
fi


python test_04_firebase_to_postgres.py
if [[ $? = 0 ]]; then
    echo "success"
else
    echo "failure: $?"
    exit
fi


python test_05_generate_stats.py
if [[ $? = 0 ]]; then
    echo "success"
else
    echo "failure: $?"
    exit
fi


python test_06_clean_up.py
if [[ $? = 0 ]]; then
    echo "success"
else
    echo "failure: $?"
    exit
fi