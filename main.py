cat > main.py << 'EOF'
import runpy
runpy.run_module("ChandMusic", run_name="__main__", alter_sys=True)
EOF
